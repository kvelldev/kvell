/**
 * Spark Repository Interface (DIP)
 *
 * Abstract definition of data access operations for Spark entities.
 */

import type { PostSparkRequest, Spark } from "@/domain/model/spark";

/**
 *
 */
export interface ISparkRepository {
  /**
   * Post a new spark.
   * @param request - The spark content to post
   * @returns The created spark details
   */
  postSpark(request: PostSparkRequest): Promise<Spark>;
}
